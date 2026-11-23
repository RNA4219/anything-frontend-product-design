# Research constraints before implementation

The frozen task/interface/cases are unchanged. Research found vendor non-equivalences that limit transfer of the future fixture results. These notes were written before the candidate implementation and any candidate score.

| Frozen fixture choice | Evidence boundary | Interpretation retained |
| --- | --- | --- |
| B03: reordered replies map by stable item identity, never reply position | AIP-233 expressly uses original request indexes for partial-failure correlation | Do not infer identity from arrival order. An API-defined original-index-to-selected-record mapping is valid; the fixture does not ban all indexes. |
| requestId is also the durable lookup reference | Graph batch id is batch-local correlation; AIP request IDs concern idempotency; AWS response IDs can be diagnostic | The fixture's identity reuse is declared, not a vendor guarantee. A service adapter must preserve distinct roles where required. |
| non-atomic item writes | AIP synchronous batch and DynamoDB transactions provide atomic counterexamples | Classify the service contract first. Do not feed atomic diagnostics into an independent-item success summary. |
| failed/blocked + unapplied:true can be retry eligible | Graph records an endpoint-specific 503 response despite successful creation | Do not derive unapplied from a general HTTP error class. The normalizer requires endpoint evidence. |
| explicit retry with fresh request ID only for eligible known-unapplied items | Safe automatic SDK retries and same-key replay exist under their own contracts | The fixture does not forbid B-IU-002's proven safe replay of an unknown original operation or require user confirmation for every transport retry. |
| lookup and cancellation exist | The inspected batch documents do not establish generic per-item lookup/cancel endpoints | B06/B11 prove only the declared fixture. Do not invent a recovery endpoint; report unresolved results and actual available routes. |
| dependency list and fixed selected total | Graph has specific dependency restrictions and a vendor batch size | Do not claim arbitrary DAG support or universal transport limits. Chunking belongs to C; the user-selected task scope remains explicit. |

Identity roles are distinct inputs: selected record, response correlation key/index, send attempt, idempotency key, durable operation reference and diagnostic request reference. Equal-looking strings are not proof that they have equal semantics.

AIP-233's request-index mapping is [B-T501](https://google.aip.dev/233). Graph's response correlation is [B-S401](https://learn.microsoft.com/en-us/graph/json-batching); throttle guidance is [B-S402](https://learn.microsoft.com/en-us/graph/throttling); endpoint and dependency exceptions are [B-S403](https://learn.microsoft.com/en-us/graph/known-issues?view=graph-rest-1.0). Atomic transaction and unprocessed-item contracts are [B-T503](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html) and [B-T502](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html). Detailed locators, read scope, source-versus-inference boundaries and hashes are in the source registry.

No fixture score, live API result, browser behavior, SDK execution or human effectiveness is asserted by these notes. Source discoveries constrain the design; they do not supply missing implementation evidence.
