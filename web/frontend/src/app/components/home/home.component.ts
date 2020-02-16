import {Component, Inject, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth/auth.service";
import {Router} from "@angular/router";
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  constructor(private authService: AuthService, private router: Router, @Inject(DOCUMENT) private document: Document) { }

  ngOnInit(): void {
  }

  login() {
    this.authService.login().then(it => {
      this.document.location.href = it['url']
    })
  }
}
