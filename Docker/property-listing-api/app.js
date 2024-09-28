const express = require("express");
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 80;

app.get("/", function(req, res) {
    const filePath = path.join(__dirname, 'office.json');
    fs.readFile(filePath, 'utf8', function(err, data) {
        if (err) {
            // Handle error if file can't be read
            console.error('Error reading the file:', err);
            return res.status(500).send('Error reading the file.');
        }
        try {
            const jsonData = JSON.parse(data);
            res.json(jsonData);  // Automatically sets Content-Type to 'application/json'
        } catch (parseError) {
            // Handle error if the JSON file is not properly formatted
            console.error('Error parsing JSON:', parseError);
            res.status(500).send('Error parsing JSON.');
        }

    });
});

app.listen(port, function(){
    console.log(`API Listening on port ${port}`);
});