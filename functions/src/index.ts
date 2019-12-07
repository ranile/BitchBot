import * as functions from 'firebase-functions';
import express = require("express")
import bodyParser = require("body-parser")
import * as admin from 'firebase-admin';
import { EmojiService } from './services/EmojiService';
import { CounterService } from './services/CountersService';

const app = express()
admin.initializeApp()

// const serviceAccount = require('../bitchbot-discordbot-firebase-adminsdk-hyo1e-bfd6127782.json');
// admin.initializeApp({
//     credential: admin.credential.cert(serviceAccount),
//     databaseURL: "https://bitchbot-discordbot.firebaseio.com"
// })

app
    .use(bodyParser.json())
    .use(bodyParser.urlencoded({ extended: false }))
    .use("/counters", require("./routes/counters"))
    .use("/emojis", require("./routes/emojis"))

const emojiService = EmojiService.getInstance()
const counterService = CounterService.getInstance()

app.get('/config', async (req, res) => {
    const config = {
        emojis: await emojiService.getAllEmojis(),
        epicEmojis: await emojiService.getEpicEmojis(),
        counterChannels: await counterService.getAllCounterChannels(),
        counters: await counterService.getAllCounters()
    }

    res.send(config)
})

const api = functions.https.onRequest(app)

module.exports = {
    api,
}