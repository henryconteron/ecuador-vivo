import test from 'node:test';
import assert from 'node:assert/strict';
import {filterTools,TASKS} from './src/workbench-model.ts';
test('processing search normalizes accents and filters by family without hiding requirements',()=>{
 const tools=[{id:'clip',label:'Recortar',kind:'vector',group:'Superposición',summary:'Polígonos',available:false,reason:'Añade otra capa'},
 {id:'zonal',label:'Estadísticas zonales',kind:'raster',group:'Ráster',summary:'Centros de píxel',available:true,reason:''}];
 assert.deepEqual(filterTools(tools,'superposicion poligonos','vector'),[tools[0]]);
 assert.deepEqual(filterTools(tools,'estadisticas','raster'),[tools[1]]);
 assert.equal(filterTools(tools,'','all').length,2);assert.deepEqual(filterTools(tools,'recortar','raster'),[]);
 assert.equal(tools[0].available,false);
});
test('data is a distinct task between navigation and processing',()=>assert.deepEqual(TASKS,['map','data','analysis','time','output']));
