var express = require('express');
var router = express.Router();
var fs = require('fs');

router.get('/', function(req, res, next) {
    let people = fs.readFileSync('people.json', 'utf8')
    console.log(people);
    res.render('index', {people: people});
});

module.exports = router;