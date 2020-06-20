import { Component, Inject, OnInit } from '@angular/core';
import { ThemePalette } from "@angular/material/core";
import { DOCUMENT } from "@angular/common";
import { HomeComponent } from "./components/home/home.component";
import {Router, RouterEvent} from "@angular/router";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    navbarColor: ThemePalette = 'primary';
    hideToolbar = false;

    constructor(
        @Inject(DOCUMENT) private document: Document,
        private router: Router
    ) {
        this.hideToolbar = this.document.location.href.toLowerCase().includes('iframe')

        this.router.events.subscribe(value => {
            if (value instanceof RouterEvent) {
                this.navbarColor = value.url && value.url != '/' ? undefined : 'primary';
            }
        })
    }

    ngOnInit(): void {
    }

    navigateToInvite() {
        this.document.location.href = HomeComponent.INVITE_URL
    }
}
