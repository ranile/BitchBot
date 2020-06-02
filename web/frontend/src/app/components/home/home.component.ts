import {Component, Inject, OnInit} from '@angular/core';
import {Router} from "@angular/router";
import {DOCUMENT} from '@angular/common';
import {UserService} from "../../services/user/user.service";
import {Stats} from "../../models/Stats";

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
    avatarUrl: string;
    static INVITE_URL = "https://discordapp.com/oauth2/authorize?client_id=595363392886145046&scope=bot&permissions=388160"
    INVITE_URL = HomeComponent.INVITE_URL // So it can be used in template
    REPO_URL = "https://www.github.com/hamza1311/BitchBot"
    DBOTS_URL = "https://discord.bots.gg/bots/595363392886145046"
    DISCORDAPPS_URL = "https://discordapps.dev/en-GB/bots/595363392886145046"
    DBL_URL = "https://top.gg/bot/595363392886145046"
    LIST_MY_BOTS_URL = "https://listmybots.com/bot/595363392886145046"
    BOTLIST_SPACE_URL = 'https://botlist.space/bot/595363392886145046';

    stats: Stats =  {
        uptime: {minutes: 0, seconds: 0, hours: 0, days: 0, human_friendly: '', total_seconds: '0'},
        commands: 0,
        users: 0,
        channels: 0,
        guilds: 0,
    };

    constructor(
        private router: Router,
        @Inject(DOCUMENT) private document: Document,
        private userService: UserService
    ) {}

    ngOnInit(): void {
        Promise.all([this.userService.fetchMyAvatarUrl(1024), this.userService.fetchMyStats()]).then(resp => {
            this.avatarUrl = resp[0]
            this.stats = resp[1]
        })
    }

    setHrefTo(url) {
        window.location.href = url
    }
}
