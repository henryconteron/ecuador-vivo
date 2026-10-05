import * as THREE from '../vendor/three-r180/three.module.min.js';
import {faultMotion,infiltrationTokens,airParcel} from './learning-science.js';

const material=color=>new THREE.MeshStandardMaterial({color,roughness:.88,metalness:0,side:THREE.DoubleSide});
function solid(geometry,color,parent){const mesh=new THREE.Mesh(geometry,material(color));parent.add(mesh);return mesh;}
function prism(points,color,parent){const shape=new THREE.Shape();points.forEach(([x,y],i)=>i?shape.lineTo(x,y):shape.moveTo(x,y));shape.closePath();const geometry=new THREE.ExtrudeGeometry(shape,{depth:2.4,bevelEnabled:false});geometry.translate(0,0,-1.2);return solid(geometry,color,parent);}
function fault(root,type){
  const left=new THREE.Group(),right=new THREE.Group();root.add(left,right);
  const bounds=[-1,-.62,-.22,.16,.24,.62,1],colors=['#795c48','#a6784f','#c3a16f','#faf5da','#ab8260','#7d9872'];
  const cut=y=>type==='strike'?0:-y/Math.sqrt(3);
  for(let i=0;i<bounds.length-1;i++){
    const lo=bounds[i],hi=bounds[i+1];
    prism([[-2,lo],[cut(lo)-.012,lo],[cut(hi)-.012,hi],[-2,hi]],colors[i],left);
    prism([[cut(lo)+.012,lo],[2,lo],[2,hi],[cut(hi)+.012,hi]],colors[i],right);
  }
  // A surface marker crossing a vertical strike-slip fault is distinct from bedding.
  if(type==='strike')for(const [g,x] of [[left,-1],[right,1]]){const mark=solid(new THREE.BoxGeometry(2,.025,.1),'#fff6d4',g);mark.position.set(x,1.025,0);}
  const direction=faultMotion(type,1),v=new THREE.Vector3(direction.x,direction.y,direction.z).normalize();
  right.add(new THREE.ArrowHelper(v,new THREE.Vector3(1.4,type==='normal'?1.8:1.35,0),.72,0xf2ce75,.18,.12));
  return (t)=>{const d=faultMotion(type,t);right.position.set(d.x,d.y,d.z);};
}
const height=(x,z)=>.18*x*x-.18*z;
function terrain(root,mountain=false){
  const geometry=new THREE.PlaneGeometry(4,3,48,36);geometry.rotateX(-Math.PI/2);
  const a=geometry.attributes.position,colors=[];
  for(let i=0;i<a.count;i++){const x=a.getX(i),z=a.getZ(i);a.setY(i,mountain?1.4*Math.exp(-x*x/.85)+.08*Math.cos(z*3):height(x,z));const c=new THREE.Color('#719582');colors.push(c.r,c.g,c.b);}
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.computeVertexNormals();
  const m=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,side:THREE.DoubleSide});root.add(new THREE.Mesh(geometry,m));
  // Vertical cut faces give the terrain a visible volume rather than a floating sheet.
  for(const z of [-1.5,1.5]){const vertices=[];for(let i=0;i<48;i++){const x=-2+i/12,n=x+1/12,y=mountain?1.4*Math.exp(-x*x/.85)+.08*Math.cos(z*3):height(x,z),ny=mountain?1.4*Math.exp(-n*n/.85)+.08*Math.cos(z*3):height(n,z);vertices.push(x,-.9,z,n,-.9,z,n,ny,z,x,-.9,z,n,ny,z,x,y,z);}const side=new THREE.BufferGeometry();side.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));side.computeVertexNormals();solid(side,'#b59870',root);}
  for(const x of [-2,2]){const vertices=[];for(let i=0;i<36;i++){const z=-1.5+i/12,n=z+1/12,y=mountain?1.4*Math.exp(-x*x/.85)+.08*Math.cos(z*3):height(x,z),ny=mountain?1.4*Math.exp(-x*x/.85)+.08*Math.cos(n*3):height(x,n);vertices.push(x,-.9,z,x,-.9,n,x,ny,n,x,-.9,z,x,ny,n,x,y,z);}const side=new THREE.BufferGeometry();side.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));side.computeVertexNormals();solid(side,'#ae9067',root);}
  const base=solid(new THREE.BoxGeometry(4,.15,3),'#735944',root);base.position.y=-.975;
  return geometry;
}
function water(root){
  const ground=terrain(root),positions=ground.attributes.position,colors=ground.attributes.color;
  const river=[];for(let i=0;i<=30;i++){const z=-1.5+i*.1;river.push(new THREE.Vector3(0,height(0,z)+.025,z));}
  solid(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(river),36,.065,8,false),'#60b4d8',root);
  const buildings=[];for(let i=0;i<6;i++){const x=-1.65+i*.6,z=-.95;const b=solid(new THREE.BoxGeometry(.28,.35,.36),'#c8c8b4',root);b.position.set(x,height(x,z)+.175,z);buildings.push(b);}
  const points=[],geo=new THREE.SphereGeometry(.044,8,6),surfaceMat=material('#57b6f1'),groundMat=material('#7ee9bf');root.userData.extraMaterials=[surfaceMat,groundMat];
  for(let i=0;i<100;i++){const p=new THREE.Mesh(geo,surfaceMat);root.add(p);points.push(p);}
  let last=-1;
  return (t,state)=>{
    const imp=state.impervious/100,infiltrating=infiltrationTokens(imp,state.wet);
    if(imp!==last){last=imp;for(let i=0;i<positions.count;i++){const color=new THREE.Color((positions.getX(i)+2)/4<imp?'#7d8990':'#719582');colors.setXYZ(i,color.r,color.g,color.b);}colors.needsUpdate=true;for(const b of buildings)b.visible=(b.position.x+2)/4<imp;}
    points.forEach((p,i)=>{
      const x=-1.8+(i%10)*.4,z=-1.3+Math.floor(i/10)*.28,y=height(x,z)+.07;
      if(t<.45){p.material=surfaceMat;p.position.set(x,THREE.MathUtils.lerp(2.7+(i%3)*.08,y,t/.45),z);}
      else{const v=(t-.45)/.55,infil=infiltrating.has(i);p.material=infil?groundMat:surfaceMat;
        p.position.set(infil?x:THREE.MathUtils.lerp(x,(i%5-2)*.045,v),infil?THREE.MathUtils.lerp(y,-.65,v):height(THREE.MathUtils.lerp(x,0,v),THREE.MathUtils.lerp(z,1.4,v))+.08,infil?z:THREE.MathUtils.lerp(z,1.35+(i%4)*.045,v));}
    });
  };
}
function sky(root){
  terrain(root,true);const parcel=new THREE.Group();root.add(parcel);
  const shell=solid(new THREE.SphereGeometry(.3,24,16),'#97d7dd',parcel);shell.material.transparent=true;shell.material.opacity=.32;shell.material.depthWrite=false;
  const cloud=new THREE.Group();parcel.add(cloud);
  for(let i=0;i<9;i++){const p=solid(new THREE.SphereGeometry(.16+(i%3)*.025,14,10),'#f9f6e9',cloud);p.position.set(Math.sin(i*2.4)*.25,Math.cos(i*1.7)*.12,Math.cos(i*2.4)*.2);}
  const curve=[];for(let i=0;i<=30;i++){const p=airParcel(i/30);curve.push(new THREE.Vector3(p.x,p.height+.55,0));}
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve),new THREE.LineDashedMaterial({color:0xc6df7e,dashSize:.1,gapSize:.07}));line.computeLineDistances();root.add(line);
  // Arrows depict ascent, not a measured wind speed.
  root.add(new THREE.ArrowHelper(new THREE.Vector3(1,.45,0).normalize(),new THREE.Vector3(-1.8,.75,.65),.7,0xc6df7e,.15,.1));
  return (t,state)=>{const p=airParcel(t,state.moist);parcel.position.set(p.x,p.height+.55,0);cloud.visible=p.condensed;shell.scale.setScalar(1+t*.35);};
}
export function createLearningWorld(canvas){
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setClearColor('#102b28');
  const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xe5fff4,0x584936,2.5));
  const light=new THREE.DirectionalLight(0xffedcc,3);light.position.set(-3,6,5);scene.add(light);
  const camera=new THREE.PerspectiveCamera(38,1,.1,100);let yaw=.65,pitch=.5,distance=9.6,targetY=.1,root=null,update=()=>{},key='';
  function dispose(){if(!root)return;const geometries=new Set(),materials=new Set(root.userData.extraMaterials||[]);root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));});geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());scene.remove(root);}
  function paint(){const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();camera.position.set(distance*Math.sin(yaw)*Math.cos(pitch),distance*Math.sin(pitch)+targetY,distance*Math.cos(yaw)*Math.cos(pitch));camera.lookAt(0,targetY,0);renderer.render(scene,camera);}
  return {set(id,state){const next=id+':'+(id==='earth'?state.fault:'');if(next!==key){dispose();key=next;root=new THREE.Group();scene.add(root);update=id==='earth'?fault(root,state.fault):id==='water'?water(root):sky(root);}targetY=id==='earth'?faultMotion(state.fault,state.progress/100).y/2:.1;update(state.progress/100,state);paint();},view(y,p,z){yaw=y;pitch=Math.max(.08,Math.min(1.48,p));distance=Math.max(5.5,Math.min(12,z));paint();},paint,dispose(){dispose();renderer.dispose();}};
}
