import {Component, Inject, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth/auth.service";
import {User} from "../../models/User";
import {UserService} from "../../services/user/user.service";
import {DOCUMENT} from "@angular/common";

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
  currentUser: User;
  showLoginButton: boolean = true;

  constructor(private authService: AuthService, private userService: UserService, @Inject(DOCUMENT) private document: Document) {
  }

  ngOnInit(): void {
    this.userService.fetchCurrentUser()
      .then(resp => {
        this.currentUser = resp.user
        this.showLoginButton = false
      })
      .catch(error => {
        if (error.status == 401) {
          this.showLoginButton = true
        }
        console.error(error)
      })
  }

  login() {
    this.authService.login().then(it => {
      this.document.location.href = it['url']
    })
  }

}
