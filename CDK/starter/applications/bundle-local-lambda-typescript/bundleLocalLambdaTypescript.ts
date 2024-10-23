// import v = require('voca');

import * as v from 'voca';

exports.handler = async function (event: any) {
    return `Hello, ${v.upperCase(event.firstName)} ${v.upperCase(event.lastName)}!`
}