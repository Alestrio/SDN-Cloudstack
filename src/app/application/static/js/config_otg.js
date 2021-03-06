/*
 * SDN-Cloudstack - API
 * Third semester project, Technical Degree, Networks and Telecommunications
 * Copyright (c) 2021-2022
 * Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
 * This code belongs exclusively to its authors, use, redistribution or
 * reproduction forbidden except with authorization from the authors.
 */
function ShowAndHide(sectionName) {
    let x = document.getElementById(sectionName);
    if (x.style.display === 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
}
function setConfig_input(config, data_type) {
    document.getElementById("config_input").value += ",\n\"" + data_type +"\":" + JSON.stringify(config, null, '\t');
}

function configNameChanged(){
    let configName = document.getElementById("configName").value;
    let submitButton = document.getElementById("submit");
    submitButton.disabled = configName.length <= 0;
}
