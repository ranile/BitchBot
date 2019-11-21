import express = require("express")
import * as admin from 'firebase-admin';

const router = express.Router()

router.get("/", async (request, response) => {
    const data = (await admin.firestore().collectionGroup('counters').get()).docs.map(it => it.data())
    const counters: any = {}
    data.forEach(counter => {
        counters[counter['name']] = counter['count']
    })
    response.send(counters)
})

router.get("/channels", async (request, response) => {
    const data = (await admin.firestore().collection(`/servers`).doc('quotesChannel').get()).data()
    response.send(data)
})

router.post("/channel", async (request, response) => {
    const body = request.body
    const snapshot = await admin.firestore().collection(`/servers`).doc('quotesChannel').get()
    const data = snapshot.data()
    if (data == undefined) { 
        response.send('data is undefined')
        return
    }
    data[body.guildId] = body.channelId

    await admin.firestore().collection(`/servers`).doc('quotesChannel').set(data)
    response.send('OK')
    
})

router.patch("/", async (request, response) => {
    const query = request.body
    const serverId = query.serverId
    const counter = query.counter
    const newValue = query.value

    await admin.firestore().collection(`/servers/${serverId}/counters/`).doc(counter).update({count: newValue})
    const snapshot = await admin.firestore().collection(`/servers/${serverId}/counters/`).doc(counter).get()
    const data = snapshot.data()

    response.send(data)
})

module.exports = router