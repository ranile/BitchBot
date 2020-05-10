import { Component, Inject, OnInit } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { DOCUMENT } from "@angular/common";
import { Router, RouterEvent } from "@angular/router";
import {ThemePalette} from "@angular/material/core";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    avatarUrl: string = '';
    navbarColor: ThemePalette = 'primary';

    constructor(
        private httpClient: HttpClient,
        @Inject(DOCUMENT) private _document: HTMLDocument,
        private router: Router) {}

    ngOnInit(): void {
        this.httpClient.get('/api/icon').toPromise().then(resp => {
            const url = resp['url']
            this.avatarUrl = url
            this._document.getElementById('appFavicon').setAttribute('href', url);
        })

        this.router.events.subscribe(value => {
            if (value instanceof RouterEvent) {
                this.navbarColor = value.url === '/home'? 'primary' : undefined;
            }
        })
    }

}
