import {FrontendRenderer,FrontendRendererArgs} from "@streamlit/component-v2-lib";
import {createRoot,Root} from "react-dom/client";
import MyComponent from "./MyComponent";
import "./style.css";
type Data={tool:string;recipe:Record<string,unknown>};
type State={artifact:unknown};
const roots=new WeakMap<FrontendRendererArgs["parentElement"],Root>();
const render:FrontendRenderer<State,Data>=({data,parentElement,setTriggerValue})=>{
 const element=parentElement.querySelector(".react-root");
 if(!element)throw new Error("No se encontró el editor científico.");
 let root=roots.get(parentElement);if(!root){root=createRoot(element);roots.set(parentElement,root)}
 root.render(<MyComponent tool={data.tool} recipe={data.recipe} onArtifact={value=>setTriggerValue("artifact",value)}/>);
 return ()=>{setTimeout(()=>{if(!element.isConnected){roots.get(parentElement)?.unmount();roots.delete(parentElement)}},0)};
};
export default render;
