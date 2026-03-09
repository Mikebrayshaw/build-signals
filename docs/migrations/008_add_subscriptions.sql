-- 008_add_subscriptions.sql
-- Stripe subscription tracking for Build Signals Pro

create table if not exists public.subscriptions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  stripe_customer_id text not null,
  stripe_subscription_id text not null,
  status text not null default 'active',
  price_id text,
  current_period_end timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- One subscription per user
create unique index if not exists idx_subscriptions_user_id on public.subscriptions(user_id);

-- Fast webhook lookups
create index if not exists idx_subscriptions_stripe_sub_id on public.subscriptions(stripe_subscription_id);

-- RLS
alter table public.subscriptions enable row level security;

-- Users can read their own subscription
create policy "Users can read own subscription"
  on public.subscriptions for select
  using (auth.uid() = user_id);

-- Service role can do everything (webhooks)
create policy "Service role full access"
  on public.subscriptions for all
  using (auth.role() = 'service_role');
