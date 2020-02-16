import { Component, OnInit } from '@angular/core';
import { UserService } from "../../services/user/user.service";

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.scss']
})
export class TestComponent implements OnInit {
  user: object;

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.userService.fetchCurrentUser().then(it => {
      this.user = it
    })
  }

}
