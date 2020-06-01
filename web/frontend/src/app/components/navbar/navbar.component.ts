import {Component, Inject, OnInit} from '@angular/core';
import {UserService} from "../../services/user/user.service";
import {DOCUMENT} from "@angular/common";
import {HomeComponent} from "../home/home.component";

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {

    constructor(private userService: UserService, @Inject(DOCUMENT) private document: Document) {}

    ngOnInit(): void {}

    navigateToInvite() {
        this.document.location.href = HomeComponent.INVITE_URL
    }

}
