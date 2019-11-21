import express = require("express")
import * as admin from 'firebase-admin';

const router = express.Router()

router.get("/all", async (request, response) => {
    const emojis = (await admin.firestore().collection('emoji').get()).docs.map(it => it.data())
    response.send(emojis)
})

router.get("/epic", async (request, response) => {
    const epicEmojis = (await admin.firestore().collection('epic_emojis').get()).docs.map(it => it.data())
    
    response.send(epicEmojis.map(it => it.command))
})

module.exports = router