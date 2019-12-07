import express = require("express")
import * as admin from 'firebase-admin';

import { CounterService } from '../services/CountersService'

const router = express.Router()
const service = CounterService.getInstance()
router.get("/", async (_, response) => {
    response.send(await service.getAllCounters())
})

router.get("/channels", async (_, response) => {
    response.send(await service.getAllCounterChannels())
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