import {
    Context,
} from 'aws-lambda';

async function helloWorld(event: any, context: Context) {
    const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
    await delay(2000) /// waiting 2 second.
    console.log('message =', ' Hello World');
    return {
        statusCode: 200
    }
}

export { helloWorld }

