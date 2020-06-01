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

    constructor(
        private userService: UserService,
        @Inject(DOCUMENT) private _document: HTMLDocument,
        private router: Router
    ) {
        this.router.events.subscribe(value => {
            if (value instanceof RouterEvent) {
                this.navbarColor = value.url === '/home'? 'primary' : undefined;
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
