import { Component, OnInit } from '@angular/core';
import { Router, RouterEvent } from "@angular/router";
import { ThemePalette } from "@angular/material/core";
import { UserService } from "./services/user/user.service";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    navbarColor: ThemePalette = 'primary';
    hideToolbar = false;

    constructor(
        private userService: UserService,
        private router: Router
    ) {
        this.router.events.subscribe(value => {
            if (value instanceof RouterEvent) {
                this.hideToolbar = value.url.toLowerCase().includes('iframe')
                this.navbarColor = value.url && value.url != '/' ? undefined : 'primary';
            }
        })
    }

    ngOnInit(): void {
    }

}
