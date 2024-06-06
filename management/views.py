from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Sum
from .models import AddRoommate, AddExpense, ExpensePaidAmount, PUBBillAmount
from datetime import datetime, date
from calendar import monthrange
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

def roommate_login(request):
    return render(request, template_name="login.html")


def login_auth(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")  
        else:
            data = {"error": "Username or Password Incorrect"}
            return render(request, "login.html", context=data)
    else:
        return redirect("/")
    
def roommate_logout(request):
    logout(request)
    return redirect("/")

def get_expense_sum(roommate, year=None, month=None):
    filters = {'name': roommate}
    if year and month:
        filters.update({'date__year': year, 'date__month': month})
    return AddExpense.objects.filter(**filters).aggregate(Sum('item_price'))['item_price__sum'] or 0

class Dashboard(View):
    template_name = "dashboard.html"

    def get_month_year(self, get_month):
        return f"{get_month} {date.today().year}"

    def get_pub_amount(self, p, roommate_count):
        return p.total_amt / roommate_count if p and roommate_count != 0 else 0

    def get_last_month_expense(self, month, year):
        return AddExpense.objects.filter(date__year=year).filter(date__month=month).aggregate(Sum("item_price"))["item_price__sum"]

    def calculate_expense(self, roommates_expense, p, pub_amt):
        if p:
            for r in roommates_expense:
                r.pub = float(pub_amt)
                r.total_paid_pub = r.food_expense + float(pub_amt)
                r.save()
        else:
            for r in roommates_expense:
                r.total_paid_pub = r.food_expense
                r.save()

    def update_balances(self, roommates_expense, group_individual):
        for chk_bal in roommates_expense:
            for gi in group_individual:
                if str(chk_bal.name).split()[-1][1:-1] == str(gi.get("name")):
                    total = chk_bal.total_paid_pub if chk_bal.total_paid_pub else 0 
                    chk_bal.purchase = gi.get("item_price__sum")
                    chk_bal.save()
                    chk_bal.balance = total - gi.get("item_price__sum")
                    chk_bal.save()
                else:
                    total = chk_bal.total_paid_pub if chk_bal.total_paid_pub else 0
                    cb_p = chk_bal.purchase
                    if not cb_p:
                        chk_bal.balance = total
                        chk_bal.save()

    def get_context_data(self, request, get_month=None):
        months = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
        }
        
        try:
            roommate_count = AddRoommate.objects.all().count()
            if roommate_count == 0:
                raise ValueError("No roommates found.")

            if get_month:
                given_month_year = self.get_month_year(get_month)
            else:
                latest_expense = ExpensePaidAmount.objects.all().last()
                given_month_year = latest_expense.month_year if latest_expense else None

            if not given_month_year:
                raise ValueError("No expense data available.")

            roommates_expense = ExpensePaidAmount.objects.filter(month_year=given_month_year)
            p = PUBBillAmount.objects.filter(food_date=given_month_year).first()
            pub_amt = self.get_pub_amount(p, roommate_count)
            month, year = given_month_year.split()
            last_month_expense = self.get_last_month_expense(months.get(month), year)
            index_pub_total = p.total_amt if p else 0

            self.calculate_expense(roommates_expense, p, pub_amt)

            group_individual = AddExpense.objects.filter(date__year=year).filter(date__month=months.get(month)).values("name").annotate(Sum("item_price"))
            self.update_balances(roommates_expense, group_individual)

            individual = roommates_expense.first() if roommates_expense else None
            year = datetime.today().year

            context = {
                "months": months,
                "datas": roommates_expense,
                "last_date": given_month_year,
                "pub_amt": pub_amt,
                "roommate": roommate_count,
                "last_month_expense": last_month_expense,
                "index_pub_total": index_pub_total,
                "individual": individual,
                "year": year,
            }
        except ValueError as e:
            context = {
                "months": months,
                "datas": "",
                "last_date": "",
                "pub_amt": 0,
                "roommate": 0,
                "last_month_expense": 0,
                "index_pub_total": 0,
                "individual": "",
                "error": str(e)
            }
        except Exception as e:
            context = {
                "months": months,
                "datas": "",
                "last_date": "",
                "pub_amt": 0,
                "roommate": 0,
                "last_month_expense": 0,
                "index_pub_total": 0,
                "individual": "",
                "error": "An unexpected error occurred."
            }
        return context

    def get(self, request):
        get_month = request.GET.get("month")
        context = self.get_context_data(request, get_month)
        return render(request, self.template_name, context)


class AddRoommateView(View):
    template_name = "addroommate.html"

    def get(self, request):
        roommates = AddRoommate.objects.all()
        context = {'roommates': roommates}
        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get("name")
        number = request.POST.get("number")
        city = request.POST.get("city")
        email = request.POST.get("email")

        if not number:
            messages.info(request, "Number is required.")
            return redirect("/add-roommate/")

        try:
            roommate = AddRoommate.objects.create(name=name, number=number, city=city, email=email)
            messages.success(request, f"{roommate.name} added as a new roommate.")
        except Exception as e:
            messages.error(request, f"Error adding roommate: {e}")

        return redirect("/add-roommate/")

class AddRoommateEdit(View):
    template_name = "addroommate.html"

    def get(self, request, pk):
        roommate = get_object_or_404(AddRoommate, id=pk)
        context = {'roommate': roommate}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        name = request.POST.get("name")
        number = request.POST.get("number")
        city = request.POST.get("city")
        email = request.POST.get("email")

        if not number:
            messages.info(request, "Number is required.")
            return redirect(f"/add-roommate/{pk}/edit/")

        try:
            roommate = get_object_or_404(AddRoommate, id=pk)
            roommate.name = name
            roommate.number = number
            roommate.city = city
            roommate.email = email
            roommate.save()
            messages.success(request, f"{roommate.name}'s information updated.")
        except Exception as e:
            messages.error(request, f"Error updating roommate: {e}")

        return redirect("/add-roommate/")


class RoommateDelete(View):
    def get(self, request, pk):
        try:
            roommate = get_object_or_404(AddRoommate, id=pk)
            roommate.delete()
            messages.success(request, f"{roommate.name} has been deleted.")
        except Exception as e:
            messages.error(request, f"Error deleting roommate: {e}")

        return redirect("/add-roommate/")


class AddExpenseView(View):
    template_name = "addexpense.html"

    def get(self, request):
        roommates = AddRoommate.objects.all()
        months = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
        }

        today = request.GET.get('month_year')
        try:
            today = datetime.strptime(today, '%Y-%m-%d')
            year = today.year
            month_name = request.GET.get("month", today.strftime("%B"))
            month = months.get(month_name)
        except:
            today = year = month_name = month = None

        if today: 
            expenses = AddExpense.objects.filter(date__year=year, date__month=month, date__day=today.day)
            this_month_expense = expenses.aggregate(Sum("item_price"))["item_price__sum"] or 0
        else:
            expenses = AddExpense.objects.all()
            this_month_expense = expenses.aggregate(Sum("item_price"))["item_price__sum"] or 0

        this_month_expense = round(this_month_expense, 2)

        context = {
            "roommates": roommates,
            "expenses": expenses,
            "this_month_expense": this_month_expense,
            "months": months,
            "selected_month": month_name,
            "year": year,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get('name')
        date_str = request.POST.get('date')
        item_name = request.POST.get('item_name')
        item_price = request.POST.get('item_price')
        month_year = request.POST.get('month_year')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            roommate = get_object_or_404(AddRoommate, id=name)
            AddExpense.objects.create(name=roommate, item_name=item_name, item_price=item_price, date=date)
            messages.success(request, f"{item_name} purchased.")

            if month_year:
                year, month = map(int, month_year.split('-'))
                chosen_month_expenses = AddExpense.objects.filter(date__year=year, date__month=month)
                total_expense = chosen_month_expenses.aggregate(Sum('item_price'))['item_price__sum'] or 0
                total_expense += float(item_price)
                chosen_month_expenses.update(total_expense=total_expense)

        except ValueError:
            messages.error(request, "Invalid date format. Please enter the date in YYYY-MM-DD format.")
        except AddRoommate.DoesNotExist:
            messages.error(request, "Roommate not found.")
        except Exception as e:
            messages.error(request, f"Error adding expense: {e}")

        return redirect("/add-expense/")


class ExpenseEdit(View):
    template_name = 'addexpense.html'

    def get(self, request, pk):
        expense = get_object_or_404(AddExpense, id=pk)
        formatted_date = expense.date.strftime("%Y-%m-%d")
        roommates = AddRoommate.objects.all()
        context = {'expense': expense, 'roommates': roommates, 'formatted_date': formatted_date}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        name = request.POST.get('name')
        date_str = request.POST.get('date')
        item_name = request.POST.get('item_name')
        item_price = request.POST.get('item_price')

        try:
            roommate = get_object_or_404(AddRoommate, id=name)
            expense = get_object_or_404(AddExpense, id=pk)
            expense.name = roommate
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            expense.item_name = item_name
            expense.item_price = item_price
            expense.save()
            messages.success(request, f"Expense for {item_name} updated.")
        except ValueError:
            messages.error(request, "Invalid date format. Please enter the date in YYYY-MM-DD format.")
        except AddRoommate.DoesNotExist:
            messages.error(request, "Roommate not found.")
        except AddExpense.DoesNotExist:
            messages.error(request, "Expense not found.")
        except Exception as e:
            messages.error(request, f"Error updating expense: {e}")

        return redirect("/add-expense/")


class ExpenseDelete(View):
    def get(self, request, pk):
        try:
            expense = get_object_or_404(AddExpense, id=pk)
            expense.delete()
            messages.success(request, "Expense deleted.")
        except Exception as e:
            messages.error(request, f"Error deleting expense: {e}")
        return redirect("/add-expense/")


clicked_month = {}


class CalculateExpense(View):
    template_name = 'calculate.html'

    def get(self, request):
        self.get_month = request.GET.get('month')
        if self.get_month:
            clicked_month["month"] = self.get_month

        months = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, 
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
        }
        current_year = date.today().year
        month_number = months.get(clicked_month.get("month"), date.today().month)
        given_month = date(current_year, month_number, 1)

        this_month_expense = AddExpense.objects.filter(date__year=given_month.year, date__month=given_month.month).aggregate(Sum("item_price"))["item_price__sum"] or 0

        roommates = AddRoommate.objects.all()
        roommate_count = roommates.count()
        per_day = (this_month_expense / roommate_count) / monthrange(given_month.year, given_month.month)[1] if roommate_count else 0

        last_day_of_month = monthrange(given_month.year, given_month.month)[1]
        no_of_days = request.GET.getlist("no_of_days")

        absent_roomies = [per_day * (last_day_of_month - int(days)) for days in no_of_days if int(days) < last_day_of_month]
        absent_roomies_amt = sum(absent_roomies)
        no_of_absent = len(absent_roomies)

        amt_to_paid = []
        for days in no_of_days:
            days_int = int(days)
            if days_int == last_day_of_month:
                amt_to_paid.append((per_day * days_int) + (absent_roomies_amt / (roommate_count - no_of_absent)))
            else:
                amt_to_paid.append(per_day * days_int)

        extract_roommate = [roommate.name for roommate in roommates]
        roommate_amt = list(zip(extract_roommate, no_of_days, [round(amt, 2) for amt in amt_to_paid]))

        if round(this_month_expense, 2) != round(sum(amt_to_paid), 2) and round(sum(amt_to_paid), 2) != 0:
            messages.error(request, f"Total Expense Not Equal - $ {sum(amt_to_paid)}")
        
        if extract_roommate and no_of_days and amt_to_paid and clicked_month.get("month"):
            for roommate, days, amt in zip(extract_roommate, no_of_days, amt_to_paid):
                person = get_object_or_404(AddRoommate, name=roommate)
                month_year = f"{clicked_month['month']} {current_year}"

                expense_paid_amount, created = ExpensePaidAmount.objects.get_or_create(
                    month_year=month_year,
                    name=person,
                    defaults={'no_of_days': days, 'food_expense': amt}
                )

                if not created:
                    expense_paid_amount.no_of_days = days
                    expense_paid_amount.food_expense = amt
                    expense_paid_amount.save()

        context = {
            "months": months,
            "year": current_year,
            "roommates": roommates,
            "get_month": clicked_month.get("month"),
            "this_month_expense": round(this_month_expense, 2),
            "per_day": round(per_day, 2),
            "last_month": last_day_of_month,
            "roommate_amt": roommate_amt,
        }
        return render(request, self.template_name, context)


class PubBill(View):
    template_name = "pub_bill.html"

    def get(self, request):
        pubbill = PUBBillAmount.objects.all().order_by('-id')
        months = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12,
        }

        month = request.GET.get("month")
        if month is not None:
            try:
                m = PUBBillAmount.objects.get(id=int(month[-1]))
                month_year = month[:-1] + " " + str(date.today().year)
                m.food_date = month_year
                m.save()
                messages.success(request, f"PUB Bill Added - {month_year}")
            except PUBBillAmount.DoesNotExist:
                messages.error(request, "Selected bill does not exist.")

        context = {
            "pubbill": pubbill,
            "months": months,
            "year": date.today().year
        }
        return render(request, self.template_name, context)

    def post(self, request):
        pre_date = request.POST.get("pre_date")
        prev_read = request.POST.get("prev_read")
        cur_date = request.POST.get("cur_date")
        cur_read = request.POST.get("cur_read")
        removal_amt = request.POST.get("removal_amt")
        water_amt = request.POST.get("water_amt")
        gst = request.POST.get("gst")

        try:
            prev_read = float(prev_read)
            cur_read = float(cur_read)
            removal_amt = float(removal_amt)
            water_amt = float(water_amt)
            gst = float(gst)
        except (ValueError, TypeError):
            messages.error(request, "Invalid input. Please enter valid numbers.")
            return redirect("/pub-bill")

        total_units = max(cur_read - prev_read, 0)
        total = (total_units * 4.50) + removal_amt + water_amt
        add_gst = (total * gst) / 100
        total += add_gst
        total = round(total, 2)

        try:
            bill = PUBBillAmount.objects.create(
                pre_date=pre_date,
                prev_read=prev_read,
                cur_date=cur_date,
                cur_read=cur_read,
                total_units=total_units,
                refuse_amt=removal_amt,
                water_amt=water_amt,
                gst=gst,
                total_amt=total
            )
            messages.success(request, "PUB Bill added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding PUB Bill: {e}")

        return redirect("/pub-bill/")

class PubBillEdit(View):
    template_name = "pub_bill.html"

    def get(self, request, pk):
        get_bill = get_object_or_404(PUBBillAmount, id=pk)
        prev_date = get_bill.pre_date.strftime('%Y-%m-%d')
        cur_date = get_bill.cur_date.strftime('%Y-%m-%d')
        context = {
            "get_bill": get_bill,
            "prev_date": prev_date,
            "cur_date": cur_date,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        pre_date = request.POST.get("pre_date")
        prev_read = request.POST.get("prev_read")
        cur_date = request.POST.get("cur_date")
        cur_read = request.POST.get("cur_read")
        removal_amt = request.POST.get("removal_amt")
        water_amt = request.POST.get("water_amt")
        gst = request.POST.get("gst")
        unit_cost = request.POST.get("unit_cost")
        total_units = abs(float(prev_read) - float(cur_read))
        
        try:
            get_bill = get_object_or_404(PUBBillAmount, id=pk)
            get_bill.pre_date = pre_date
            get_bill.prev_read = prev_read
            get_bill.cur_date = cur_date
            get_bill.cur_read = cur_read
            get_bill.refuse_amt = removal_amt
            get_bill.water_amt = water_amt
            get_bill.gst = gst
            get_bill.unit_cost = unit_cost
            get_bill.total_units = total_units
            
            total = (float(total_units) * float(unit_cost)) + float(removal_amt) + float(water_amt)
            add_gst = (total * float(gst)) / 100
            total = total + add_gst
            get_bill.total_amt = total
            
            get_bill.save()
            messages.success(request, "PUB Bill updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating PUB Bill: {e}")

        return redirect("/pub-bill/")


class PubBillDelete(View):
    template_name = "pub_bill.html"

    def get(self, request, pk):
        try:
            bill = get_object_or_404(PUBBillAmount, id=pk)
            bill.delete()
            messages.success(request, "PUB Bill deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting PUB Bill: {e}")

        return redirect("/pub-bill/")