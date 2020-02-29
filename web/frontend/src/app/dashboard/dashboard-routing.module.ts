import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ModDashboardComponent } from "./components/mod-dashboard/mod-dashboard.component";
import {MainDashboardComponent} from "./components/main-dashboard/main-dashboard.component";


const routes: Routes = [
    {
        path: 'dashboard', component: MainDashboardComponent, children: [
            { path: '', redirectTo: '/', pathMatch: 'full' },
            { path: 'mod', component: ModDashboardComponent, },
        ]
    }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class DashboardRoutingModule {
}
