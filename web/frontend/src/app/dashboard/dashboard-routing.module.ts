import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ModDashboardComponent } from "./components/mod-dashboard/mod-dashboard.component";
import { MainDashboardComponent } from "./components/main-dashboard/main-dashboard.component";
import { ShowAllRemindersComponent } from "./components/reminders/show-all-reminders/show-all-reminders.component";


const routes: Routes = [
    /*{
        path: 'dashboard', component: MainDashboardComponent, children: [
            { path: '', redirectTo: 'mod', pathMatch: 'full' },
            { path: 'mod', component: ModDashboardComponent, },
            { path: 'reminders', component: ShowAllRemindersComponent, },
        ]
    }*/
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class DashboardRoutingModule {
}
