import { Component, Inject, OnInit } from '@angular/core';
import { DOCUMENT } from "@angular/common";
import { Router, RouterEvent } from "@angular/router";
import { ThemePalette } from "@angular/material/core";
import { UserService } from "./services/user/user.service";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    avatarUrl: string = '';
    navbarColor: ThemePalette = 'primary';
    hideToolbar = false;

    constructor(
        private userService: UserService,
        @Inject(DOCUMENT) private _document: HTMLDocument,
        private router: Router
    ) {
        this.router.events.subscribe(value => {
            if (value instanceof RouterEvent) {
                this.hideToolbar = value.url.toLowerCase().includes('hidetoolbar')
                this.navbarColor = value.url && !value.url.includes('/home')? undefined : 'primary';

            }
        })
    }

    ngOnInit(): void {
        this.userService.fetchMyAvatarUrl(1024).then(url => {
            this.avatarUrl = url
            this._document.getElementById('appFavicon').setAttribute('href', url);
        })
    }

}
