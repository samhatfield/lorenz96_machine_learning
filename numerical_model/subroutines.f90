! (C) Copyright 2009-2016 ECMWF.
!
! This software is licensed under the terms of the Apache Licence Version 2.0
! which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
! In applying this licence, ECMWF does not waive the privileges and immunities
! granted to it by virtue of its status as an intergovernmental organisation nor
! does it submit to any jurisdiction.

!> Prepare for an integration of the QG model.

!> At the start of a timestep of the QG model, the state must contain
!! streamfunction, potential vorticity and wind components. The control
!! variable for the analysis, however, contains only streamfunction.
!! This routine calculates potential vorticity and wind from the
!! streamfunction, and is called before an integration of the QG model.

subroutine prepare_integration(x, x_north, x_south, rs, q_out, u_out, v_out)

use qg_constants, only: nx, ny, f1, f2, deltax, deltay, bet

implicit none

!f2py integer, intent(aux) :: nx, ny
real(8), intent(in) :: x(nx,ny,2)
real(8), intent(in) :: x_north(2)
real(8), intent(in) :: x_south(2)
real(8), intent(in) :: rs(nx,ny)

real(8), intent(out) :: q_out(nx,ny,2)
real(8), intent(out) :: u_out(nx,ny,2)
real(8), intent(out) :: v_out(nx,ny,2)

! -- calculate potential vorticity and wind components

call calc_pv(nx, ny, q_out, x, x_north, x_south, f1, f2, deltax, deltay, bet, rs)
call zonal_wind(u_out, x, x_north, x_south, nx, ny, deltay)
call meridional_wind(v_out, x, nx, ny, deltax)

end subroutine prepare_integration
