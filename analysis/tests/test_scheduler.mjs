import assert from 'node:assert/strict';
import {runBounded,evidenceGate,researchStatus,validateTasks} from '../revised-skills/frugal-fable/scripts/scheduler.mjs';
let tests=0;
async function test(name,fn){await fn();tests++;console.log("PASS "+name);}
const task=(id='one',bound=50)=>({id,upperBound:bound,tier:'construction',
  scratch:'.frugal-fable/run-one/'+id+'.json',highStakes:true,requiresVerification:true});
const result=t=>({path:t.scratch,evidencePresent:true,verifyPassed:true,reviewPassed:true});
await test('reserve concurrent headroom before calls',async()=>{
  let release;const barrier=new Promise(r=>release=r);let calls=0;
  const pending=runBounded([task('one',60),task('two',60)],{capTokens:100,maxCalls:2,maxConcurrency:2},async t=>{
    calls++;await barrier;return {totalTokens:60,result:result(t)};
  });
  await Promise.resolve();assert.equal(calls,1);release();
  const r=await pending;assert.equal(r.accountedTokens,60);assert.equal(r.results.filter(x=>x.status==='skipped').length,1);
});
await test('release reservation using actual total usage',async()=>{
  const r=await runBounded([task('one',60),task('two',60)],{capTokens:100,maxCalls:2,maxConcurrency:1},
    async t=>({totalTokens:20,result:result(t)}));
  assert.equal(r.calls,2);assert.equal(r.accountedTokens,40);
});
await test('missing usage charges reservation and fails',async()=>{
  const r=await runBounded([task()],{capTokens:100,maxCalls:1,maxConcurrency:1},async t=>({result:result(t)}));
  assert.equal(r.accountedTokens,50);assert.equal(r.measuredTotalTokens,0);assert.equal(r.estimatedChargedTokens,50);assert.equal(r.accountingComplete,false);assert.equal(r.results[0].status,'failed');
});
await test('adapter breach stops subsequent launch',async()=>{
  const r=await runBounded([task('one'),task('two')],{capTokens:200,maxCalls:2,maxConcurrency:1},
    async t=>({totalTokens:70,result:result(t)}));
  assert.equal(r.breached,true);assert.equal(r.calls,1);assert.equal(r.accountedTokens,70);
});
await test('failed or missing verification is rejected',async()=>{
  for(const key of ['verifyPassed','reviewPassed','evidencePresent']){
    let r=result(task());delete r[key];assert.equal(evidenceGate(task(),r),false);
    r=result(task());r[key]=false;assert.equal(evidenceGate(task(),r),false);
  }
});
await test('stopped work and wrong output cannot pass',async()=>{
  assert.equal(evidenceGate(task(),{...result(task()),stoppedShort:true}),false);
  assert.equal(evidenceGate(task(),{...result(task()),path:'/outside'}),false);
});
await test('split and missing research votes stay unresolved',async()=>{
  const v=x=>({verdict:x,evidence:'primary page excerpt'});
  assert.equal(researchStatus([v('support'),v('refute')]),'disputed');
  assert.equal(researchStatus([v('support'),null]),'unknown');
  assert.equal(researchStatus([v('support'),v('support')]),'supported-pending-source-review');
});
await test('unknown tiers duplicate IDs and traversal rejected',async()=>{
  assert.throws(()=>validateTasks([{...task(),tier:'typo'}]));
  assert.throws(()=>validateTasks([task(),task()]));
  assert.throws(()=>validateTasks([{...task(),scratch:'../outside'}]));
});
await test('invalid budgets rejected before adapter',async()=>{
  for(const value of [NaN,Infinity,-1,0,1.2]){
    await assert.rejects(runBounded([task()],{capTokens:value,maxCalls:1,maxConcurrency:1},async()=>{}));
  }
});
await test('calls retries and synthesis reserve bounded',async()=>{
  const r=await runBounded([task('one',50),task('two',50)],{capTokens:100,reserveTokens:30,maxCalls:1,maxConcurrency:1},
    async()=>{throw new Error('inert failure');});
  assert.equal(r.calls,1);assert.equal(r.accountedTokens,50);assert.equal(r.results.filter(x=>x.status==='failed').length,1);
});
console.log(JSON.stringify({tests,passed:tests}));
