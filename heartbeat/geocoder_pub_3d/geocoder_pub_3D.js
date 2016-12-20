var psv = d3.dsv("|", "text/plain");

Plotly.d3.psv('https://raw.githubusercontent.com/bcgov/dbcrss/master/heartbeat/src/test.txt', function(err, rows){
      function unpack(rows, key) {
          return rows.map(function(row) 
          { return row[key]; }); }
var x = unpack(rows , 'x');
var y = unpack(rows , 'y');
var z = unpack(rows , 'z'); 
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
