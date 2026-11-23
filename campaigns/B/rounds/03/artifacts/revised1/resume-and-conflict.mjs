// Illustrative task controller. The caller supplies trusted current session/capability.
// This is not an authentication system, secure-storage boundary or HTTP implementation.
const copy = value => structuredClone(value);
export function createResumableEdit(api, {session, saved, targetResourceId=saved.resourceId,
  nextId, recoveryAction=null}={}) {
  let activeSession=copy(session),record=copy(saved),epoch=0,phase='not_started';
  let observedResource=null,reviewed=null,operationOutcome=null,operationResult=null;
  let resourceReadError='',message='',needsAuth=false;
  const outcomes=new Map();
  const terminal=result=>result?.status==='succeeded'||result?.status==='conflict'||
    (result?.status==='failed'&&result.terminal===true&&result.unapplied===true);
  const restored=record.confirmedOutcome;
  if(restored&&restored.ownerId===record.ownerId&&restored.resourceId===record.resourceId&&
    restored.operationId===record.operation?.id&&terminal(restored.result))
    outcomes.set(restored.operationId,copy(restored.result));
  const seenIds=new Set(record.operation?[record.operation.id]:[]);
  function guard(){
    if(!activeSession?.authenticated||needsAuth)return 'reauthenticate';
    if(activeSession.accountId!==record.ownerId)return 'different_account';
    if(targetResourceId!==record.resourceId)return 'different_task';
    if(!activeSession.canRead)return 'no_access';
    return null;
  }
  const current=e=>e===epoch&&!guard();
  const identity=()=>({accountId:activeSession.accountId,resourceId:record.resourceId});
  const editable=()=>!guard()&&activeSession.canWrite&&['editing','conflict','review'].includes(phase);
  const tokenValid=()=>typeof observedResource?.etag==='string'&&observedResource.etag.length>0;
  function setSession(value){activeSession=copy(value);needsAuth=false;epoch++;observedResource=null;reviewed=null;resourceReadError='';phase=guard()||'not_started';}
  async function readCurrent(e){
    try{const resource=await api.load(identity());if(current(e)){observedResource=copy(resource);resourceReadError='';}}
    catch{if(current(e)){observedResource=null;resourceReadError='現在の資源状態を照合できません。確認済みの操作結果とは別の問題です。';}}
  }
  function retainOutcome(result,operation){
    // A correlated operation fact can be retained without applying it to another view.
    if(operation&&terminal(result)&&!outcomes.has(operation.id))outcomes.set(operation.id,copy(result));
  }
  async function accept(result,e,operation){
    retainOutcome(result,operation);
    if(!current(e))return;
    // A late pending read cannot undo a terminal fact already observed for this operation.
    result=outcomes.get(operation?.id)??result;
    if(result?.status==='succeeded'){
      operationOutcome='succeeded';operationResult=copy(result.operationResult??null);phase='completed';
      message='対象の操作が成功したことを確認しました。操作時の結果と、照合した資源状態を分けて表示します。';
      await readCurrent(e);return;
    }
    if(result?.status==='conflict'){
      operationOutcome='conflict';operationResult=null;record.operation=null;reviewed=null;
      observedResource=result.observed?copy(result.observed):null;
      if(!observedResource)await readCurrent(e);
      if(current(e)){phase=activeSession.canWrite?'conflict':'readonly';message='対象が変更されています。入力は保持しています。比較して確認し直してください。';}
      return;
    }
    if(result?.status==='failed'&&result.terminal===true&&result.unapplied===true){
      operationOutcome='failed';record.operation=null;reviewed=null;await readCurrent(e);
      if(current(e)){phase=activeSession.canWrite?'editing':'readonly';message='この操作は成立しない終端結果を確認しました。次の判断に必要な現在状態を照合してください。';}return;
    }
    if(result?.status==='auth_required'){needsAuth=true;phase='reauthenticate';return;}
    operationOutcome=null;operationResult=null;phase=result?.status==='pending'?'pending':'unknown';
    message=phase==='pending'?'同じ操作の結果を待っています。':'操作記録から結果を確認できません。新規送信せず、照合経路を使ってください。';
  }
  async function resume(){
    const blocked=guard();if(blocked){phase=blocked;return;}
    const e=++epoch;phase='loading';reviewed=null;observedResource=null;resourceReadError='';
    if(record.operation){
      const operation=copy(record.operation);
      try{const result=outcomes.get(operation.id)??await api.lookup({...identity(),operationId:operation.id});await accept(result,e,operation);}
      catch{if(current(e)){phase='unknown';message='操作結果の照会に失敗しました。元の結果は未確認です。';}}
      return;
    }
    await readCurrent(e);if(!current(e))return;
    if(!observedResource){phase='unavailable';message='現在の状態を確認してから再開してください。';return;}
    if(!activeSession.canWrite){phase='readonly';message='現在の権限では閲覧のみ可能です。下書きを自動送信しません。';return;}
    phase=record.lastKnown?.etag&&record.lastKnown.etag!==observedResource.etag?'conflict':'editing';
    message=phase==='conflict'?'保存時から対象が変わっています。入力と観測した値を比較してください。':'未送信の入力を復帰しました。まだサーバーへ保存していません。';
  }
  function edit(field,value){if(!editable()||!Object.hasOwn(record.draft,field))return false;record.draft[field]=value;reviewed=null;phase='editing';return true;}
  function review(){if(!editable()||!tokenValid())return false;reviewed={etag:observedResource.etag,changes:copy(record.draft)};phase='review';message='観測した状態と今回の変更内容を確認してください。';return true;}
  function canCommit(){return !guard()&&activeSession.canWrite&&phase==='review'&&reviewed&&tokenValid()&&reviewed.etag===observedResource.etag&&JSON.stringify(reviewed.changes)===JSON.stringify(record.draft);}
  async function commit(){
    if(!canCommit())return;
    const id=nextId();if(typeof id!=='string'||!id||seenIds.has(id)){phase='editing';message='新しい操作を準備できません。送信せず入力を保持しています。';return;}
    seenIds.add(id);const operation={id,changes:copy(reviewed.changes),baseEtag:reviewed.etag};record.operation=operation;
    const e=++epoch;phase='pending';operationOutcome=null;operationResult=null;
    try{await accept(await api.update({...identity(),requestId:id,ifMatch:operation.baseEtag,changes:copy(operation.changes)}),e,operation);}
    catch{if(current(e)){phase='unknown';message='応答を受け取れず結果未確認です。同じ操作を照合してください。';}}
  }
  function view(){
    const blocked=guard(),visible=!blocked;
    const text=blocked==='reauthenticate'?'再認証が必要です。保存した作業の成否は、この状態だけでは変わりません。':blocked==='different_account'?'このアカウントでは保存した作業を表示・再開できません。':blocked==='different_task'?'この画面の対象と保存した作業が一致しません。':blocked==='no_access'?'現在の権限ではこの作業を表示できません。':message;
    return copy({phase:blocked||phase,message:text,draft:visible?record.draft:null,lastKnown:visible?record.lastKnown:null,
      observedResource:visible?observedResource:null,operationId:visible?record.operation?.id??null:null,
      operationOutcome:visible?operationOutcome:null,operationResult:visible?operationResult:null,
      resourceReadError:visible?resourceReadError:'',canCommit:Boolean(canCommit()),canReview:editable()&&tokenValid(),
      canResume:visible,recoveryAction:visible?recoveryAction:null});
  }
  function snapshot(){
    const saved=copy(record),operation=record.operation;
    saved.confirmedOutcome=operation&&outcomes.has(operation.id)?{ownerId:record.ownerId,
      resourceId:record.resourceId,operationId:operation.id,result:copy(outcomes.get(operation.id))}:null;
    return saved;
  }
  return {resume,edit,review,commit,setSession,view,snapshot};
}
