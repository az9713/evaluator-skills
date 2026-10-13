// Provider-neutral reservation scheduler. No provider calls, shell or filesystem access.
const positive = (n,label) => {
  if (!Number.isSafeInteger(n) || n<=0) throw new TypeError(label+" must be positive integer");
  return n;
};
export function validateTasks(tasks) {
  if (!Array.isArray(tasks)) throw new TypeError("tasks must be an array");
  const seen=new Set();
  for (const t of tasks) {
    if (!t || !/^[a-z0-9][a-z0-9-]{0,63}$/.test(t.id) || seen.has(t.id)) throw new TypeError("invalid/duplicate task id");
    seen.add(t.id); positive(t.upperBound,"upperBound");
    if (!["economy","construction","judgment"].includes(t.tier)) throw new TypeError("unknown tier");
    if (typeof t.scratch!=="string" || !/^\.frugal-fable\/[a-z0-9-]+\/[a-z0-9-]+\.(json|md|txt)$/.test(t.scratch)) throw new TypeError("unsafe scratch path");
    if (typeof t.highStakes!=="boolean" || typeof t.requiresVerification!=="boolean") throw new TypeError("explicit gate booleans required");
  }
}
export function evidenceGate(task,result) {
  if (!result || result.path!==task.scratch || result.stoppedShort===true) return false;
  if (task.requiresVerification && result.verifyPassed!==true) return false;
  if (task.highStakes && result.reviewPassed!==true) return false;
  return result.evidencePresent===true;
}
export function researchStatus(votes) {
  if (!Array.isArray(votes) || votes.length!==2) return "unknown";
  if (!votes.every(v=>v && ["support","refute","unknown"].includes(v.verdict) && typeof v.evidence==="string" && v.evidence.trim())) return "unknown";
  if (votes.some(v=>v.verdict==="unknown")) return "unknown";
  if (votes.every(v=>v.verdict==="support")) return "supported-pending-source-review";
  if (votes.every(v=>v.verdict==="refute")) return "refuted";
  return "disputed";
}
export async function runBounded(tasks,options,adapter) {
  validateTasks(tasks);
  const cap=positive(options.capTokens,"capTokens");
  const maxCalls=positive(options.maxCalls,"maxCalls");
  const concurrency=positive(options.maxConcurrency,"maxConcurrency");
  const reserve=options.reserveTokens??0;
  if (!Number.isSafeInteger(reserve) || reserve<0 || reserve>=cap) throw new TypeError("invalid reserve");
  if (typeof adapter!=="function") throw new TypeError("explicit adapter required");
  let spent=0,measured=0,estimated=0,reserved=0,calls=0,breached=false;
  const results=[];
  const active=new Set();
  async function launch(task) {
    let charge=task.upperBound,usageKnown=false;
    try {
      const response=await adapter(task,{maxTotalTokens:task.upperBound});
      const usage=response?.totalTokens;
      if (!Number.isSafeInteger(usage) || usage<0) throw new Error("missing/invalid total usage");
      charge=usage; usageKnown=true;
      if (usage>task.upperBound) {
        breached=true;
        results.push({id:task.id,status:"failed",reason:"adapter breached reservation",usage,usageBasis:"measured"});
      } else {
        results.push({id:task.id,status:evidenceGate(task,response.result)?"accepted":"rejected",usage,usageBasis:"measured",result:response.result});
      }
    } catch(error) {
      results.push({id:task.id,status:"failed",reason:String(error),usage:charge,usageBasis:usageKnown?"measured":"estimated-reservation"});
    } finally { reserved-=task.upperBound; spent+=charge; if(usageKnown)measured+=charge;else estimated+=charge; }
  }
  for (const task of tasks) {
    while(active.size>=concurrency) await Promise.race(active);
    if (breached || calls>=maxCalls || spent+reserved+task.upperBound>cap-reserve) {
      results.push({id:task.id,status:"skipped",reason:breached?"adapter contract breached":"call or reservation limit"}); continue;
    }
    // Reserve synchronously BEFORE invoking the adapter or admitting another task.
    reserved+=task.upperBound; calls++;
    const pending=launch(task);
    active.add(pending);
    pending.then(()=>active.delete(pending));
  }
  await Promise.all(active);
  return {accountedTokens:spent,measuredTotalTokens:measured,estimatedChargedTokens:estimated,accountingComplete:estimated===0,calls,breached,reserveTokens:reserve,results,
          limitType:"admission reservations; provider ceiling requires enforcing adapter"};
}
