import {Component, HostListener, Inject, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth/auth.service";
import {Router} from "@angular/router";
import {DOCUMENT} from '@angular/common';
import {UserService} from "../../services/user/user.service";

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
    avatarUrl: string;

    constructor(
        private authService: AuthService,
        private router: Router,
        @Inject(DOCUMENT) private document: Document,
        private userService: UserService
    ) {
    }

    ngOnInit(): void {
        this.document.getElementById('icon-container').style.opacity = '0';

        this.userService.fetchMyAvatarUrl(1024).then(it => {
            this.avatarUrl = it
        })
    }

    login() {
        this.authService.login().then(it => {
            this.document.location.href = it['url']
        })
    }

    navigateToOauthPage() {
        window.location.href = "https://discordapp.com/oauth2/authorize?client_id=595363392886145046&scope=bot&permissions=388160"
    }

    lastTopValue = 0

    @HostListener('window:scroll', [])
    onScroll() {
        const rect = this.document.getElementById('two').getBoundingClientRect().top
        console.log(window.innerHeight, rect, this.lastTopValue)
        if (this.lastTopValue >= (window.innerHeight / 1.7)) {
            this.document.getElementById('icon-container').style.opacity = '0';
            this.document.getElementById('info-content').style.opacity = '1';
        } else {
            this.document.getElementById('icon-container').style.opacity = '1';
            this.document.getElementById('info-content').style.opacity = '0';
        }
        this.lastTopValue = rect
    }

    navigateToGithubRepo() {
        window.location.href = "https://www.github.com/hamza1311/BitchBot"
    }
}
