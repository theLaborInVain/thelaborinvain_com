import { Component, OnInit } from '@angular/core';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-index',
  standalone: true,
  imports: [],
  templateUrl: './index.component.html',
  styleUrl: './index.component.scss'
})

export class IndexComponent implements OnInit {
  environment = environment;
  ngOnInit() {
    console.log('App initialized!');
    console.log('Production mode:', environment.production);
  }
}
