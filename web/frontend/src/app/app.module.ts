import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import {HttpClientModule} from "@angular/common/http";
import { NavbarComponent } from './components/navbar/navbar.component';
import { ShowWarnsComponent } from './components/show-warns/show-warns.component';
import { ModDashboardComponent } from './dashboard/components/mod-dashboard/mod-dashboard.component';
import {FormsModule} from "@angular/forms";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonModule} from "@angular/material/button";
import {MatToolbarModule} from "@angular/material/toolbar";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatListModule} from "@angular/material/list";
import {MatTabsModule} from "@angular/material/tabs";
import {MatOptionModule} from "@angular/material/core";
import {MatSelectModule} from "@angular/material/select";
import { ShowWarnComponent } from './components/show-warn/show-warn.component';
import {MatCardModule} from "@angular/material/card";
import { RelativeTimePipe } from './pipes/relative-time.pipe';
import { DiscordUserPipe } from './pipes/discord-user.pipe';
import { DashboardComponent } from './dashboard/components/dashboard/dashboard.component';
import {DashboardModule} from "./dashboard/dashboard.module";

@NgModule({
    declarations: [
        AppComponent,
        HomeComponent,
        NavbarComponent,
        ShowWarnsComponent,
        ModDashboardComponent,
        DashboardComponent,
        ShowWarnComponent,
        RelativeTimePipe,
        DiscordUserPipe,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        BrowserAnimationsModule,
        MatButtonModule,
        MatToolbarModule,
        MatSidenavModule,
        MatListModule,
        MatTabsModule,
        MatOptionModule,
        MatSelectModule,
        MatCardModule,
        DashboardModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule {
}
