import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
// const serviceAccount = require('../bitchbot-discordbot-firebase-adminsdk-hyo1e-bfd6127782.json');

admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    // credential: admin.credential.cert(serviceAccount),
    databaseURL: "https://bitchbot-discordbot.firebaseio.com"
})

export const allEmojis = functions.https.onRequest(async (request, response) => {
    const data = await admin.firestore().collection('emoji').get()
    const list = data.docs
    const emojis = list.map(it => it.data())
    response.send(emojis)
})

export const saveUserInfo = functions.https.onRequest(async (request, response) => {
    const userInfo = request.body
    try {
        await admin.firestore().collection('users').doc(userInfo.id).set(userInfo)
        response.send('OK')
    } catch (error) {
        response.send('error')
    }
})


export const getUserInfo = functions.https.onRequest(async (request, response) => {
    const userid = request.query.id
    try {
        const snapshot = await admin.firestore().collection('users').doc(userid).get()
        const data = snapshot.data()
        response.send(data)
    } catch (error) {
        response.send(error)
    }
})

export const epicEmojis = functions.https.onRequest(async (request, response) => {
    const emojis = await admin.firestore().collection('epic_emojis').get()
    const list = emojis.docs.map(it => it.data())
    response.send(list)
})
