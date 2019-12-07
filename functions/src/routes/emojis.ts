import express = require("express")
import { EmojiService } from "../services/EmojiService"

const router = express.Router()
const service = EmojiService.getInstance()

router.get("/all", async (request, response) => {
    response.send(await service.getAllEmojis())
})

router.get("/epic", async (request, response) => {
    response.send(await service.getEpicEmojis())
})

module.exports = router