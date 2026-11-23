# SESSION C coverage map

Base: `3d02174a69676afa8e0b02f4062cc6ecb636d300`. Initial inventory has shared routing and booking fixture, but no C module.

| Area | Initial state | Priority | Verification target |
| --- | --- | --- | --- |
| Component semantics, state and keyboard | Missing executable instruction contract | P0 | Native control activation, availability, dialog focus, close paths |
| Responsive layout and input | Missing reusable acceptance rules | P1 | 320 CSS px reflow, local overflow, reading order, target geometry |
| Tokens and preferences | Missing dependency and runtime contracts | P1 | Alias failure, themes, system color and motion preferences |
| Async UI rendering and notification | Missing stable state-to-DOM mapping | P1 | Busy/result/error semantics without focus loss |
| Browser/AT matrix | Not verified | P2 | Explicit supported engines and manual screen-reader evidence |
| IME / hydration / composite widgets | Unresearched | P2–3 | Dedicated follow-up fixtures |

## Scope boundary

Art Direction owns palette, type, spacing aesthetics and composition. Its existing browser/accessibility/form references are reused, not relabeled as new discoveries. C adds component input/output contracts, state-to-DOM implementation decisions and executable checks across variants. A owns feature/IA decisions; B owns business transitions and recovery policies; D owns evaluation design and release acceptance. C tests implementation behavior only and hands off business policy gaps.
