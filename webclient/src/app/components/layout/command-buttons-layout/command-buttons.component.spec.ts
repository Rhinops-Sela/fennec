import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CommandButtonsComponent } from './command-buttons.component';

describe('CommandButtonsComponent', () => {
  let component: CommandButtonsComponent;
  let fixture: ComponentFixture<CommandButtonsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CommandButtonsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CommandButtonsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
