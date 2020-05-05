import {Component, Inject, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth/auth.service";
import {UserService} from "../../services/user/user.service";
import {DOCUMENT} from "@angular/common";
import {HomeComponent} from "../home/home.component";

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
    /*currentUser: User;
    isLoggedIn: boolean = false;*/

    constructor(private authService: AuthService, private userService: UserService, @Inject(DOCUMENT) private document: Document) {
    }

    ngOnInit(): void {
        /*this.userService.fetchCurrentUser()
            .then(resp => {
                this.currentUser = resp.user
                this.isLoggedIn = true
            })
            .catch(error => {
                if (error.status == 401) {
                    this.isLoggedIn = false
                }
                console.error(error)
            })*/
    }

    /*login() {
        this.authService.login().then(it => {
            this.document.location.href = it['url']
        })
    }

    logout() {
        this.authService.logout().then(() => {
            this.isLoggedIn = false
            //  TODO: Navigate to /home
        })
    }*/

    navigateToInvite() {
        this.document.location.href = HomeComponent.INVITE_URL
    }

}
