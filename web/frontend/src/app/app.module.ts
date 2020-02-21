import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { TestComponent } from './components/test/test.component';
import {HttpClientModule} from "@angular/common/http";
import { NavbarComponent } from './components/navbar/navbar.component';
import { ShowWarnsComponent } from './components/show-warns/show-warns.component';
import { ModDashboardComponent } from './components/mod-dashboard/mod-dashboard.component';
import {FormsModule} from "@angular/forms";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonModule} from "@angular/material/button";

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TestComponent,
    NavbarComponent,
    ShowWarnsComponent,
    ModDashboardComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    MatButtonModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
