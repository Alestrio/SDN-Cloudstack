/*
 * SDN-Cloudstack - API
 * Third semester project, Technical Degree, Networks and Telecommunications
 * Copyright (c) 2021-2022
 * Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
 * This code belongs exclusively to its authors, use, redistribution or
 * reproduction forbidden except with authorization from the authors.
 */

function setCurrentConfig(room, config) {
    let config_h2 = document.getElementById("selected_config");
    config_h2.innerHTML = "Configuration sélectionnée : " + config;
    let apply_button = document.getElementById("apply");
    let delete_button = document.getElementById("delete");
    // post request to set the config
    apply_button.action = "/config/" + room + "/" + config;
    delete_button.action = "/config/delete/" + room + "/" + config;
}

