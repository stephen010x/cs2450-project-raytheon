
function uploadFiles(input_id) {
    const file_input = document.getElementById(input_id);
    const files = file_input.files
    const formdata = new FormData();

    // add files to formdata
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formdata.append('files[]', file);
    }

    // send formdata, and fetch the links to the upload files
    // on the server, and return them.
    return fetch ('/upload', {
        method: 'POST',
        body: formdata
    })
    .then(response => response.json())
    .then(data => {
        return data;
    })
    .catch(error => {
        console.error('Error Uploading File(s):', error);
        return null;
    });
}
