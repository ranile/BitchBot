import { Component, Inject, OnInit } from '@angular/core';
import { ThemePalette } from "@angular/material/core";
import { DOCUMENT } from "@angular/common";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    navbarColor: ThemePalette = 'primary';
    hideToolbar = false;

    constructor(@Inject(DOCUMENT) private document: Document) {
        const location = this.document.location
        this.hideToolbar = location.href.toLowerCase().includes('iframe')
        this.navbarColor = location.pathname && location.pathname != '/' ? undefined : 'primary';
    }

    ngOnInit(): void {
    }

}
