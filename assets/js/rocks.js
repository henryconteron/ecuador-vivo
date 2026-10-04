document.getElementById("rock-print").addEventListener("click", () => window.print());
document.getElementById("rock-download").addEventListener("click", () => {
  const record = {type:"ecuador-vivo-rock-observation", version:1, exported:new Date().toISOString(), status:"user-observation-not-validated", fields:Object.fromEntries(new FormData(document.getElementById("rock-form")))};
  const url = URL.createObjectURL(new Blob([JSON.stringify(record,null,2)], {type:"application/json"}));
  const link = document.createElement("a"); link.href=url; link.download="ecuador-vivo-observacion-roca.json"; link.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
  document.getElementById("rock-status").textContent=document.documentElement.lang==="en"?"Download requested. Check your browser downloads.":"Descarga solicitada. Revisa las descargas del navegador.";
});
