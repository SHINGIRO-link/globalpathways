# Payment integration research

## Verified official findings

| Provider | Verified capability | Integration implication |
| --- | --- | --- |
| MTN MoMo | The official MoMo API overview describes Collections for remote automatic collection of bills, fees, and taxes. It also lists a Collection Widget, tutorials for RequestToPay, and transaction-status queries. | Use a server-side payment initiation endpoint and reconcile final status from provider responses/status checks. Do not mark a payment successful from the browser alone. |
| Airtel Money | The official Airtel Africa developer portal currently requires selecting a specific operating company/country before proceeding. The visible country list includes Uganda, Kenya, Tanzania, Rwanda, Madagascar, DRC, Gabon, Zambia, Chad, Niger, Malawi, Congo-B, and Seychelles. | Airtel integration is country-specific. The production country, merchant account, currency, and collection API credentials must be confirmed before enabling a live provider adapter. |

## Architecture decision

The application should create a payment record only after an application is submitted and accepted for review. The UI may offer MoMo and Airtel as provider choices, but the server must create the payment request, store the provider reference, and reconcile the final status through a verified callback/status mechanism. Secrets must be configured through project environment settings. Until the user supplies the operating country, currency, and merchant credentials, the implementation should remain in sandbox/demo mode and must not claim that money was received.

## Sources

1. MTN MoMo API overview: https://momo.mtn.com/api/
2. Airtel Africa Developer Portal: https://developers.airtel.africa/developer
