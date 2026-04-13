/**
 * fantasy-sports plugin — core library.
 *
 * Implements draft analysis, trade evaluation, and waiver wire
 * recommendation logic from the corresponding SKILL.md files.
 */

export {
  analyzeTrade,
  type TradeInput,
  type TradeResult,
} from './trade.js';
export {
  rankWaiverAdds,
  type WaiverCandidate,
  type RankedWaiverAdd,
} from './waiver.js';
export {
  draftStrategy,
  type DraftContext,
  type DraftPlan,
} from './draft.js';
