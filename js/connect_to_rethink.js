//const r = require('rethinkdb');
//
//r.connect({ host: 'localhost', port: 8080, timeout: 60, db: 'RTDB_desync'}, (err, conn) => {
//  if (err) {
//    console.error(err);
//    return;
//  }
//  console.log('Connected to RethinkDB');
//});

const r = require('rethinkdb');

r.connect({ host: 'rethinkdb', port: 8080, timeout: 60, db: 'RTDB_desync'}, (err, conn) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log('Connected to RethinkDB');
});