import {Component, Inject, OnInit} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {DOCUMENT} from "@angular/common";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit  {
  title = 'bitch-bot';
  avatarUrl: string = '';

  constructor(private httpClient: HttpClient, @Inject(DOCUMENT) private _document: HTMLDocument) {
  }

  ngOnInit(): void {
    this.httpClient.get('/api/icon').toPromise().then(resp => {
      const url = resp['url']
      this.avatarUrl = url
      this._document.getElementById('appFavicon').setAttribute('href', url);
    })
  }

}
