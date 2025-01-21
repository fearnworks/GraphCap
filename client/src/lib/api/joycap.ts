export async function generateCaptions(mountId: string) {
    // const response = await fetch(`/joycap/generate-captions`, {
    //     method: 'POST',
    //     body: JSON.stringify({ mountId })
    // });
    console.log('Client Generate Captions', { mountId });
    return { caption: 'test' };
}
