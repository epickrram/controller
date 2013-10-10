$(document).ready(function() {
    var timeoutId;
    $( "#tags" ).autocomplete({
      source: getMatchingTags
    });
    $('#status').text('ready');
    function postSearch(searchTerm, responseCallback) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: 'search',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({query: searchTerm})
        }).done(function(result) {
            var valArray = [];
            for(var i = 0; i < result.matches.length; i++) { 
                var entry = result.matches[i].tag + '(' + result.matches[i].size + ')';
                valArray.push(entry)
            }
            responseCallback(valArray);
        });
    }

    function getMatchingTags(request, response) {
        postSearch(request.term, response);
    }

    function getServerStatus() {
         $.ajax({
            type: 'POST',
            dataType: 'json',
            url: 'status',
            contentType: 'application/json; charset=utf-8'
        }).done(function(result) {
            $('#status').text('Player status: ' + result.text);
            if(result.text === 'IDLE' || result.text === 'PLAYING') {
                var queueHtml = '<span>Playlist</span><ul>';
                for(var i = 0; i < result.playQueue.length; i++) {
                    var queueEntry = result.playQueue[i];
                    queueHtml += '<li><b>' + queueEntry.tag + '</b></li>';
                    queueHtml += '<ul>';
                    for(var j = 0; j < queueEntry.fileList.length; j++) {
                        queueHtml += '<li>' + queueEntry.fileList[j] + '</li>';

                    }
                    queueHtml += '</ul>';
                }
                queueHtml += '</ul>';
                if(result.playQueue.length !== 0) {
                    $('#playQueue').html(queueHtml);
                }
                else {
                    $('#playQueue').html('');
                }
                if(result.currentlyPlaying !== 'None') {
                    $('#currentSong').html('Now playing: ' + result.currentlyPlaying);
                }
                else {
                    $('#currentSong').html('');
                }
            }
            if(timeoutId !== undefined) {
                clearTimeout(timeoutId);
            }
            timeoutId = setTimeout(getServerStatus, 3000);
        });
       
    }

    $( ".selector" ).on( "autocompleteselect", function( event, ui ) {
        var originalTag = event.srcElement.value.split('(')[0]
          $.ajax({
            type: 'POST',
            dataType: 'json',
            url: 'selection',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({ query: originalTag })
        }).done(function(result) {
            //$('#tags').clear();
            var foo = $('#tags')
            foo[0].value = '';
            getServerStatus();
        });
       
    });

    getServerStatus();
    $('.selector').focus();
});
