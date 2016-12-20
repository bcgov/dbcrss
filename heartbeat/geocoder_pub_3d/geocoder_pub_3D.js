Plotly.d3.csv('https://raw.githubusercontent.com/bcgov/dbcrss/master/heartbeat/src/test2.csv', function(err, rows){
      function unpack(rows, key) {
          return rows.map(function(row) 
          { return row[key]; }); }
          
var x = unpack(rows , 'chart');
var y = unpack(rows , 'date');
var z = unpack(rows , 'y'); 
var c = unpack(rows , 'color');
Plotly.plot('graph', [{
  type: 'scatter3d',
  mode: 'lines',
  x: x,
  y: y,
  z: z,
  opacity: 1,
  line: {
    width: 6,
    color: c,
    reversescale: false
  }
}], {
  height: 640
});
});
