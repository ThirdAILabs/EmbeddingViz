import appEvents from '../service/appEvents.js';
import request from '../service/request.js';
import scene from '../store/scene.js'
import clientRuntime from '../runtime/clientRuntime.js';
import config from '../../config.js'

import SearchResultWindowViewModel from './SearchResultWindowViewModel.js';

export default searchBoxModel();

const searchResultsWindowId = 'search-results';

function update_samples(response) {
    console.log(response);
    var results = response["Result"];
    console.log(results);
    var searchResults = []
    for (var i = 0; i < results.length; i++) {
        var title = results[i]["TITLE"];
        console.log(title);
        var product_id = results[i]["PRODUCT_ID"];
        console.log(product_id);
        var query = product_id + '-' + title;
        console.log(query);
        var search_results = scene.find(query);
        console.log(search_results);
        if (search_results.length > 0) {
            searchResults.push(search_results[0]);
        }
    }
    console.log(searchResults);
    var searchResultWindowViewModel = new SearchResultWindowViewModel(searchResults);

    if (searchResults.length) {
        appEvents.showNodeListWindow.fire(searchResultWindowViewModel, searchResultsWindowId);
    } else {
        appEvents.hideNodeListWindow.fire(searchResultsWindowId);
    }
}

function searchBoxModel() {
    let api = {
        search: search,
        submit: submit
    };

    return api;

    function search(newText) {
        if (newText && newText[0] === ':') return; // processed in submit

        request(
            config.apiUrl + '?query=' + newText + "&k=5", {
                responseType: 'json'
            }).then(update_samples);

        return;

        var searchResults = scene.find(newText);
        var searchResultWindowViewModel = new SearchResultWindowViewModel(searchResults);

        if (searchResults.length) {
            appEvents.showNodeListWindow.fire(searchResultWindowViewModel, searchResultsWindowId);
        } else {
            appEvents.hideNodeListWindow.fire(searchResultsWindowId);
        }
    }

    function submit(command) {
        if (!command || command[0] !== ':') return; // We can handle only commands here

        // Yes, this is not secure, I know
        command = 'with (ctx) { ' + command.substr(1) + ' }';
        var dynamicFunction = new Function('ctx', command);
        dynamicFunction(clientRuntime);
    }
}
