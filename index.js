const getAudioFile = async () => {
    // call api with the file name present in `url` input field
    const url = document.getElementById('url').value;

    const response = fetch(`/extract-audio?youtube_url=${url}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );
    debugger;
}
