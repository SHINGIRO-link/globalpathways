import { useEffect, useRef, useState } from "react";
import { CheckCircle2, CreditCard, Loader2, XCircle } from "lucide-react";
import { getApplicationStatus, preparePayment, ServiceUnavailableError } from "@/lib/api";

type PaymentPhase = "idle" | "requesting" | "pending" | "paid" | "failed";

/**
 * Normalize a Rwandan mobile-money number to IntouchPay's expected
 * 12-digit MSISDN format, e.g. "250788XXXXXX". Returns null when the
 * input cannot be turned into a valid number.
 */
export function normalizeRwandaPhone(raw: string): string | null {
  const digits = raw.replace(/\D/g, "");
  let msisdn = "";
  if (digits.length === 12 && digits.startsWith("250")) msisdn = digits;
  else if (digits.length === 10 && digits.startsWith("0")) msisdn = `250${digits.slice(1)}`;
  else if (digits.length === 9 && digits.startsWith("7")) msisdn = `250${digits}`;
  else return null;
  // Rwanda mobile numbers are 2507XXXXXXXX (MTN/Airtel).
  return /^2507\d{8}$/.test(msisdn) ? msisdn : null;
}

const POLL_INTERVAL_MS = 4000;
const MAX_POLLS = 24; // ~96s of polling before we stop and let the user re-check.

export default function PaymentForm({
  email,
  applicationId,
  initialPhone = "",
  onPaid,
}: {
  email: string;
  applicationId: number;
  initialPhone?: string;
  onPaid?: () => void;
}) {
  const [phone, setPhone] = useState(initialPhone);
  const [phase, setPhase] = useState<PaymentPhase>("idle");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  useEffect(() => () => stopPolling(), []);

  function startPolling() {
    stopPolling();
    let attempts = 0;
    pollRef.current = setInterval(async () => {
      attempts += 1;
      try {
        const result = await getApplicationStatus(email, applicationId);
        const status = result.payment?.status;
        if (status === "paid") {
          stopPolling();
          setPhase("paid");
          setMessage("Payment confirmed. Thank you — your application is now being processed.");
          onPaid?.();
        } else if (status === "failed") {
          stopPolling();
          setPhase("failed");
          setError("The payment was not completed. You can try again.");
        }
      } catch {
        // Ignore transient polling errors; the interval will retry.
      }
      if (attempts >= MAX_POLLS && pollRef.current) {
        stopPolling();
        setMessage(
          "Still waiting for confirmation. If you approved the prompt, use Refresh in a moment to update the status.",
        );
      }
    }, POLL_INTERVAL_MS);
  }

  async function requestPayment() {
    setError("");
    setMessage("");
    const msisdn = normalizeRwandaPhone(phone);
    if (!msisdn) {
      setError("Enter a valid Rwandan mobile money number, e.g. 0788 123 456.");
      return;
    }
    setPhase("requesting");
    try {
      const result = await preparePayment(email, applicationId, msisdn);
      if (result.payment?.status === "paid") {
        setPhase("paid");
        setMessage("Payment confirmed. Thank you — your application is now being processed.");
        onPaid?.();
        return;
      }
      setPhase("pending");
      setMessage(result.message || "Payment request sent. Approve the prompt on your phone (dial *182*7*1# if it does not appear).");
      startPolling();
    } catch (requestError) {
      setPhase("idle");
      setError(
        requestError instanceof ServiceUnavailableError
          ? requestError.message
          : requestError instanceof Error
            ? requestError.message
            : "We could not send the payment request. Please check the number and try again.",
      );
    }
  }

  if (phase === "paid") {
    return (
      <div className="payment-ready payment-ready-success">
        <div className="payment-ready-icon"><CheckCircle2 size={19} /></div>
        <div>
          <span className="eyebrow">Payment complete</span>
          <h4>Service fee received</h4>
          <p>{message}</p>
        </div>
      </div>
    );
  }

  const busy = phase === "requesting" || phase === "pending";

  return (
    <div className="payment-ready">
      <div className="payment-ready-icon"><CreditCard size={19} /></div>
      <div>
        <span className="eyebrow">Next step · service fee</span>
        <h4>Pay the 2,000 RWF service fee</h4>
        <p>Enter your MTN MoMo or Airtel Money number. You will approve the payment prompt on your phone.</p>
        <label>Mobile money number
          <input
            value={phone}
            onChange={event => setPhone(event.target.value)}
            placeholder="0788 123 456"
            inputMode="tel"
            disabled={busy}
          />
        </label>
        <div className="provider-row">
          <button className="button button-dark compact" onClick={requestPayment} disabled={busy || !phone.trim()}>
            {phase === "requesting" ? <><Loader2 size={15} className="spin" /> Sending request…</>
              : phase === "pending" ? <><Loader2 size={15} className="spin" /> Waiting for approval…</>
                : "Pay 2,000 RWF"}
          </button>
        </div>
        {message && <small className="payment-note">{message}</small>}
        {error && <small className="payment-note payment-note-error"><XCircle size={13} /> {error}</small>}
      </div>
    </div>
  );
}
